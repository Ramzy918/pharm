# Generated for enhanced order fields and rating system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_order_auto_shipped_at_productrating_and_more'),
    ]

    operations = [
        # Add fields to Order model
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=20, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=254, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=120, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='commune',
            field=models.CharField(blank=True, max_length=120, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='detailed_address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='postal_code',
            field=models.CharField(blank=True, max_length=16, default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(blank=True, max_length=20, default='domicile'),
        ),
        migrations.AddField(
            model_name='order',
            name='auto_shipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
        # Add status for auto-shipping
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'En attente'),
                    ('CONFIRMED', 'Confirmée'),
                    ('SHIPPED', 'Expédiée'),
                    ('DELIVERED', 'Livrée'),
                    ('CANCELLED', 'Annulée')
                ],
                default='PENDING',
                max_length=16
            ),
        ),
        
        # Create ProductRating model if not exists
        migrations.CreateModel(
            name='ProductRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.product')),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_rating')
                ]
            },
        ),
    ]
