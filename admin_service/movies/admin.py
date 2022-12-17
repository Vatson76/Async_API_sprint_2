from django.contrib import admin
from .models import Genre, GenreFilmwork, Filmwork, Person, PersonFilmwork
from django.utils.translation import gettext_lazy as _
from rangefilter.filter import DateRangeFilter


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description', 'id', 'created', 'modified')
    search_fields = ('name', 'description')
    list_filter = ('created', 'modified')
    ordering = ['name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created', 'modified')
    search_fields = ('full_name', 'description', 'created', 'modified')
    list_filter = ('created', 'modified')
    ordering = ['full_name']


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    verbose_name = _("Filmwork's genre")
    verbose_name_plural = _("Filmwork's genres")


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ['person']
    verbose_name = _('Person in filmwork')
    verbose_name_plural = _('People in filmwork')


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    autocomplete_fields = ('persons', 'genres')
    list_display = ('title', 'type', 'creation_date', 'rating', 'get_genres', 'get_persons', 'created', 'modified')
    list_filter = ('type', ('creation_date', DateRangeFilter), 'genres')
    search_fields = ('title', 'description', 'id')

    list_prefetch_related = ('genres',)

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .prefetch_related(*self.list_prefetch_related)
        )
        return queryset

    def get_genres(self, obj):
        return ','.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = _('genres')

    def get_persons(self, obj):
        return ', '.join(
            [str(person) for person in obj.persons.all()]
        )
    get_persons.short_description = _('persons')
