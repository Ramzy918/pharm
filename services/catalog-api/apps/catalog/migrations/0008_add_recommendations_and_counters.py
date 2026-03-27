# Generated for recommendations and product counters

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_add_order_fields_and_ratings'),
    ]

    operations = [
        # Add ProductRecommendation model
        migrations.CreateModel(
            name='ProductRecommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_recommendation')
                ]
            },
        ),
        
        # Add counters to Product model
        migrations.AddField(
            model_name='product',
            name='user_likes',
            field=models.PositiveIntegerField(default=0),
        ),
        
        migrations.AddField(
            model_name='product',
            name='user_recommendations',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
