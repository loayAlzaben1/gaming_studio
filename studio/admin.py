from django.contrib import admin
from .models import Donation, Game, Photo, Video, DevlogVideo, TeamMember

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('image', 'caption')
    show_change_link = True

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ('title', 'video_url')
    show_change_link = True

class DevlogVideoInline(admin.TabularInline):
    model = DevlogVideo
    extra = 1
    fields = ('title', 'video_url', 'description', 'content', 'author', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'release_date', 'is_featured')
    inlines = [PhotoInline, VideoInline, DevlogVideoInline]
    search_fields = ('title', 'platform')
    list_filter = ('platform', 'release_date', 'is_featured')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'platform', 'release_date', 'is_featured')
        }),
        ('Media', {
            'fields': ('cover_image', 'trailer_link')
        }),
    )

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'amount', 'donated_at')
    actions = ['reset_donations']
    search_fields = ('donor_name',)
    list_filter = ('donated_at',)

    def reset_donations(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "You do not have permission to reset donations.", level='error')
            return
        total = Donation.objects.all().delete()
        self.message_user(request, f"Successfully reset {total[0]} donations. Total is now $0.00.", level='success')

    reset_donations.short_description = "Reset all donations to $0.00"

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')
    fields = ('name', 'role', 'bio', 'photo', 'social_link')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('caption', 'game')
    search_fields = ('caption',)
    list_filter = ('game',)
    fields = ('image', 'caption', 'game')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'game')
    search_fields = ('title',)
    list_filter = ('game',)
    fields = ('title', 'video_url', 'game')

@admin.register(DevlogVideo)
class DevlogVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('game', 'created_at')
    fields = ('title', 'video_url', 'description', 'content', 'author', 'game')
    readonly_fields = ('created_at',)