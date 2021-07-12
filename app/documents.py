from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Player, Team, TransferList


@registry.register_document
class PlayerDocument(Document):
    team = fields.ObjectField(properties={
        'name': fields.TextField(),
        'country': fields.TextField(),
    })

    class Index:
        # Name of the elastic search index
        name = 'players'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Player
        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'country',
            'first_name',
            'last_name',
            'price'
        ]

        related_models = [Team, ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(PlayerDocument, self).get_queryset().select_related(
            'team'
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Player instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Team):
            return related_instance.players.all()


@registry.register_document
class TransferListDocument(Document):
    player = fields.ObjectField(properties={
        # 'first_name': fields.TextField(),
        # 'last_name': fields.TextField(),
        'name': fields.TextField(attr='name'),
        'country': fields.TextField(),
        'team': fields.ObjectField(properties={
                'name': fields.TextField(),
                'country': fields.TextField(),
            })
    })

    class Index:
        # Name of the elastic search index
        name = 'transfer_list'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = TransferList
        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'asking_price',
        ]

        related_models = [Player, ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(TransferListDocument, self).get_queryset().select_related(
            'player'
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Player instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Player):
            return related_instance.transfer_offer
