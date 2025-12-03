from django.db import migrations

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS banner CASCADE;
            DROP TABLE IF EXISTS carousel CASCADE;
            DROP TABLE IF EXISTS product CASCADE;
            """,
            reverse_sql="""
            -- no reverse
            """
        )
    ]
