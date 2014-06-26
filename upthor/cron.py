from upthor.management.commands.clean_temporary_files import Command


try:
    from django_cron import CronJobBase, Schedule
except ImportError:
    pass
else:
    class CleanTemporaryFiles(CronJobBase):
        RUN_EVERY_MINS = 30  # every 30 minutes

        schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
        code = 'upthor.CleanTemporaryFiles'

        def do(self):
            Command.clean_temporary_files()
