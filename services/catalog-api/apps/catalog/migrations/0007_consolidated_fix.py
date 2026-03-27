from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_order_auto_shipped_at_productrating_and_more'),
    ]

    operations = [
        # Add Order fields
        migrations.AddField(model_name='order', name='phone', field=models.CharField(blank=True, max_length=20, default='')),
        migrations.AddField(model_name='order', name='email', field=models.EmailField(blank=True, max_length=254, default='')),
        migrations.AddField(model_name='order', name='city', field=models.CharField(blank=True, max_length=120, default='')),
        migrations.AddField(model_name='order', name='commune', field=models.CharField(blank=True, max_length=120, default='')),
        migrations.AddField(model_name='order', name='detailed_address', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='order', name='postal_code', field=models.CharField(blank=True, max_length=16, default='')),
        migrations.AddField(model_name='order', name='delivery_method', field=models.CharField(blank=True, max_length=20, default='domicile')),
        
        # ProductRating changes
        migrations.RenameField(model_name='productrating', old_name='score', new_name='rating'),
        migrations.AddField(model_name='productrating', name='comment', field=models.TextField(blank=True, default='')),
        
        # Create ProductRecommendation
        migrations.CreateModel(
            name='ProductRecommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_user_id', models.PositiveIntegerField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='catalog.product')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=['auth_user_id', 'product'], name='unique_user_product_recommendation')]},
        ),
        
        # Add Product fields (counters)
        migrations.AddField(model_name='product', name='user_likes', field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name='product', name='user_recommendations', field=models.PositiveIntegerField(default=0)),
    ]
