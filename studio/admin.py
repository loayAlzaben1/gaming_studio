from django.contrib import admin
from .models import (Donation, Game, Photo, Video, DevlogVideo, TeamMember, SponsorTier, 
                     DonationGoal, ContactMessage, UserProfile, Achievement, UserAchievement, UserActivity)
from django.utils.html import format_html

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
    list_display = ('donor_name', 'amount', 'sponsor_tier', 'donation_type', 'is_recurring', 'donated_at', 'thank_you_sent')
    list_filter = ('donation_type', 'is_recurring', 'sponsor_tier', 'donated_at', 'thank_you_sent')
    search_fields = ('donor_name', 'donor_email')
    readonly_fields = ('donated_at', 'sponsor_tier')
    
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_email')
        }),
        ('Donation Details', {
            'fields': ('amount', 'donation_type', 'is_recurring', 'donation_goal')
        }),
        ('System Information', {
            'fields': ('sponsor_tier', 'donated_at', 'thank_you_sent', 'paypal_subscription_id', 'next_payment_date'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_thank_you_emails', 'reset_donations']
    
    def send_thank_you_emails(self, request, queryset):
        sent = 0
        for donation in queryset.filter(donor_email__isnull=False, thank_you_sent=False):
            donation.send_thank_you_email()
            sent += 1
        self.message_user(request, f'Thank you emails sent to {sent} donors.')
    send_thank_you_emails.short_description = 'Send thank you emails to selected donations'

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

@admin.register(SponsorTier)
class SponsorTierAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'min_amount', 'color_display', 'icon')
    list_editable = ('min_amount',)
    ordering = ('min_amount',)
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'min_amount')
        }),
        ('Display Settings', {
            'fields': ('color', 'icon', 'perks'),
            'description': 'Customize how this tier appears to users'
        }),
    )

@admin.register(DonationGoal)
class DonationGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'current_amount', 'target_amount', 'progress_display', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'description')
    readonly_fields = ('current_amount', 'progress_percentage', 'is_completed')
    
    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = '#10B981' if percentage >= 100 else '#3B82F6' if percentage >= 50 else '#F59E0B'
        return format_html(
            '<div style="width: 100px; background-color: #E5E7EB; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background-color: {}; display: flex; align-items: center; justify-content: center; color: white; font-size: 11px;">'
            '{:.1f}%'
            '</div></div>',
            min(percentage, 100),
            color,
            percentage
        )
    progress_display.short_description = 'Progress'
    
    actions = ['mark_completed', 'mark_active']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} goal(s) marked as completed.')
    mark_completed.short_description = 'Mark selected goals as completed'
    
    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} goal(s) marked as active.')
    mark_active.short_description = 'Mark selected goals as active'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'target_amount', 'image')
        }),
        ('Progress', {
            'fields': ('current_amount', 'progress_percentage', 'is_completed'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('status', 'end_date')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'message_preview')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_level', 'total_donated', 'current_tier', 'experience_points', 'login_streak')
    list_filter = ('current_tier', 'account_level', 'is_premium', 'join_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('join_date', 'total_donated', 'account_level', 'experience_points')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('Gaming Stats', {
            'fields': ('account_level', 'experience_points', 'login_streak', 'last_login_date', 'favorite_game')
        }),
        ('Donation Info', {
            'fields': ('total_donated', 'total_donations_count', 'current_tier', 'is_premium')
        }),
        ('Social Stats', {
            'fields': ('profile_views', 'comments_count', 'likes_received')
        }),
        ('Timestamps', {
            'fields': ('join_date',)
        }),
    )

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'experience_reward', 'is_rare', 'color_display')
    list_filter = ('is_rare', 'experience_reward')
    search_fields = ('name', 'description', 'type')
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;"><i class="{}"></i> {}</span>',
            obj.color,
            obj.icon,
            obj.color
        )
    color_display.short_description = 'Color'

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_date', 'is_showcased')
    list_filter = ('achievement', 'earned_date', 'is_showcased')
    search_fields = ('user__username', 'achievement__name')
    readonly_fields = ('earned_date',)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'timestamp', 'experience_gained')
    list_filter = ('activity_type', 'timestamp', 'experience_gained')
    search_fields = ('user__username', 'description')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')