import base64
import mimetypes

from django.db import migrations, models


def backfill_photo_data(apps, schema_editor):
    Profile = apps.get_model("user", "Profile")
    for profile in Profile.objects.filter(photo_data__isnull=True, photo__isnull=False).exclude(photo=""):
        try:
            profile.photo.open("rb")
            raw = profile.photo.read()
            profile.photo.close()
        except Exception:
            continue

        mime_type = mimetypes.guess_type(profile.photo.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(raw).decode("ascii")
        profile.photo_data = f"data:{mime_type};base64,{encoded}"
        profile.save(update_fields=["photo_data"])


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_chatmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="photo_data",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_photo_data, migrations.RunPython.noop),
    ]
