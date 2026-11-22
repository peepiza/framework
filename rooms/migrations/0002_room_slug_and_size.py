from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    rooms = Room.objects.using(schema_editor.connection.alias)
    for room in rooms.iterator():
        stem = slugify(room.name)[:80].strip("-_") or "room"
        room.slug = f"{stem}-{room.pk}"
        room.save(using=schema_editor.connection.alias, update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("rooms", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="room", name="slug",
            field=models.SlugField("Слаг", max_length=120, null=True, editable=False),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="room", name="slug",
            field=models.SlugField("Слаг", max_length=120, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name="room", name="is_large",
            field=models.GeneratedField(
                verbose_name="Помещение на 50 человек и больше",
                expression=models.Case(
                    models.When(capacity__gte=50, then=models.Value(True)),
                    default=models.Value(False),
                ),
                output_field=models.BooleanField(), db_persist=True,
            ),
        ),
    ]
