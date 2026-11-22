from django.db import migrations, models


def forwards(apps, schema_editor):
    Rehearsal = apps.get_model("rehearsals", "Rehearsal")
    Rehearsal.objects.using(schema_editor.connection.alias).filter(
        is_cancelled=True,
    ).update(status="cancelled")


def backwards(apps, schema_editor):
    Rehearsal = apps.get_model("rehearsals", "Rehearsal")
    Rehearsal.objects.using(schema_editor.connection.alias).filter(
        status="cancelled",
    ).update(is_cancelled=True)


class Migration(migrations.Migration):
    dependencies = [("rehearsals", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="rehearsal", name="status",
            field=models.CharField(
                "Статус", max_length=10, default="active",
                choices=[
                    ("active", "Активна"), ("cancelled", "Отменена"),
                    ("completed", "Завершена"),
                ],
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="rehearsal", name="is_cancelled"),
    ]
