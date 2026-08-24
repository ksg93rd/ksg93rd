"""Run logging. Every meaningful operation leaves an auditable RUN record."""
import os

from . import ids, records, security


class Run(object):
    def __init__(self, root, objective, trigger="cli", agent=None, skill=None,
                 inputs=None, demo=False):
        self.root = root
        self.id = ids.new_id("run")
        self.objective = objective
        self.trigger = trigger
        self.agent = agent
        self.skill = skill
        self.inputs = list(inputs or [])
        self.demo = demo
        self.started_at = ids.now_iso()
        self.records_read = []
        self.records_created = []
        self.records_modified = []
        self.warnings = []
        self.errors = []
        self.retry_count = 0
        self.validation_result = "not-run"
        self.review_result = "not-run"
        self.notes = []
        self.path = None
        # Write the run record immediately, as `running`. Two reasons:
        # records created during the run reference run_id, so the target must
        # already exist; and a run that crashes still leaves evidence.
        self._persist("running")

    def _persist(self, status):
        meta = {
            "id": self.id, "type": "run",
            "title": self.objective[:120],
            "status": status,
            "created_at": self.started_at, "updated_at": ids.now_iso(),
            "trust_level": "internal",
            "objective": self.objective, "trigger": self.trigger,
            "started_at": self.started_at,
            "agent": self.agent or "vault-cli", "skill": self.skill,
            "inputs": self.inputs,
            "records_read": self.records_read,
            "records_created": self.records_created,
            "records_modified": self.records_modified,
            "validation_result": self.validation_result,
            "review_result": self.review_result,
            "warnings": self.warnings, "errors": self.errors,
            "retry_count": self.retry_count,
        }
        if status != "running":
            meta["completed_at"] = ids.now_iso()
            meta["final_status"] = status
        if self.demo:
            meta["demo"] = True
        body = "## Objective\n\n%s\n\n## Notes\n\n%s\n" % (
            self.objective,
            "\n".join("- " + n for n in self.notes) or "(none)")
        record = records.save(self.root, meta, body, path=self.path)
        self.path = record.path
        return record

    def created(self, record_id):
        if record_id and record_id not in self.records_created:
            self.records_created.append(record_id)

    def modified(self, record_id):
        if record_id and record_id not in self.records_modified:
            self.records_modified.append(record_id)

    def read(self, record_id):
        if record_id and record_id not in self.records_read:
            self.records_read.append(record_id)

    def warn(self, message):
        self.warnings.append(_scrub(message))

    def error(self, message):
        self.errors.append(_scrub(message))

    def note(self, message):
        self.notes.append(_scrub(message))

    def finish(self, status="success"):
        if self.errors and status == "success":
            status = "partial"
        self._persist(status)
        return self.id


def _scrub(message):
    """Never write a credential into a run log, even 'for completeness'."""
    text = str(message)
    for _rule, _sev, pattern in security.SECRET_PATTERNS:
        import re
        text = re.sub(pattern, "[REDACTED-SECRET]", text)
    return text
