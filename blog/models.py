# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.db import models
from django.utils.safestring import mark_safe
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name
from taggit.models import TaggedItemBase
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                MultiFieldPanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.blocks import (CharBlock, FieldBlock,
                                        RawHTMLBlock, RichTextBlock,
                                        StreamBlock, StructBlock, TextBlock)
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet


# Create your models here.


class CodeBlock(blocks.StructBlock):
    """
    Code Highlighting Block
    """
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('bash', 'Bash/Shell'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('scss', 'SCSS'),
        ('json', 'JSON'),
    )

    STYLE_CHOICES = (
        ('autumn', 'autumn'),
        ('borland', 'borland'),
        ('bw', 'bw'),
        ('colorful', 'colorful'),
        ('default', 'default'),
        ('emacs', 'emacs'),
        ('friendly', 'friendly'),
        ('fruity', 'fruity'),
        ('github', 'github'),
        ('manni', 'manni'),
        ('monokai', 'monokai'),
        ('murphy', 'murphy'),
        ('native', 'native'),
        ('pastie', 'pastie'),
        ('perldoc', 'perldoc'),
        ('tango', 'tango'),
        ('trac', 'trac'),
        ('vim', 'vim'),
        ('vs', 'vs'),
        ('zenburn', 'zenburn'),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    style = blocks.ChoiceBlock(choices=STYLE_CHOICES, default='syntax')
    code = blocks.TextBlock()

    class Meta:
        icon = 'code'

    def render(self, value, context):
        src = value['code'].strip('\n')
        lang = value['language']
        lexer = get_lexer_by_name(lang)
        css_classes = ['code', value['style']]

        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass=' '.join(css_classes),
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'),
        ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class GeneralStreamBlock(StreamBlock):
    paragraph = RichTextBlock(icon="pilcrow")
    intro = RichTextBlock(icon="pilcrow")
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")
    code = CodeBlock()


class BlogIndexPage(Page):
    intro = StreamField(GeneralStreamBlock(), null=True)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    @property
    def posts(self):
        # Get list of live blog pages that are descendants of this page
        posts = Post.objects.live().descendant_of(self)
        # Order by most recent date first
        posts = posts.order_by('-date')
        return posts

    def get_context(self, request):
        # Get blogs
        posts = self.posts
        tags = PostTag.objects.all()
        categories = PostCategory.objects.all()
        # Filter by tag
        tag = request.GET.get('tag')
        category = request.GET.get('category')
        if category:
            posts = posts.filter(categories__name=category)
        if tag:
            posts = posts.filter(tags__name=tag)
        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(posts, 10)  # Show 10 blogs per page
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['posts'] = posts
        context['categories'] = categories
        context['tags'] = tags
        return context

    api_fields = ['header_image', 'intro']


BlogIndexPage.content_panels = [
    ImageChooserPanel('header_image'),
    FieldPanel('title', classname="full title"),
    StreamFieldPanel('intro', classname="full"),
]


class PostTag(TaggedItemBase):
    content_object = ParentalKey('Post', related_name='tagged_items')


class Post(Page):
    date = models.DateField("Post date")
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro = models.CharField(max_length=250)
    body = StreamField(GeneralStreamBlock(), null=True)
    tags = ClusterTaggableManager(through=PostTag, blank=True)
    categories = ParentalManyToManyField('blog.PostCategory', blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    api_fields = ['header_image', 'intro']

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Post information"),
        ImageChooserPanel('header_image'),
        FieldPanel('title', classname="full title"),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
    ]


@register_snippet
class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'post categories'
