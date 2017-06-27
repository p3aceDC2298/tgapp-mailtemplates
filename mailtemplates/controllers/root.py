# -*- coding: utf-8 -*-
"""Main Controller"""
import tg
from mailtemplates.lib.validator import KajikiTemplateValidator
from tg import TGController
from tg import config
from tg import expose, flash, require, url, lurl, request, redirect, validate
from tg.decorators import paginate
from tg.i18n import ugettext as _
from mailtemplates.lib.forms import CreateTranslationForm, EditTranslationForm, NewModelForm

from mailtemplates import model


class RootController(TGController):
    @expose('kajiki:mailtemplates.templates.index')
    @expose('genshi:mailtemplates.templates.index')
    @paginate('mail_models', items_per_page=tg.config.get('pagination.item_per_page', 20))
    def index(self):
        __, mail_models = model.provider.query(model.MailModel, filters=dict())
        return dict(mail_models=mail_models)

    @expose('kajiki:mailtemplates.templates.index')
    @expose('genshi:mailtemplates.templates.index')
    @paginate('mail_models', items_per_page=tg.config.get('pagination.item_per_page', 20))
    def mail_model(self, id, translation):
        __, mail_models = model.provider.query(model.MailModel, filters=dict())
        return dict(mail_models=mail_models)

    @expose('kajiki:mailtemplates.templates.new_translation')
    @expose('genshi:mailtemplates.templates.new_translation')
    def new_translation(self, model_id, **kwargs):
        return dict(form=CreateTranslationForm, values=dict(model_id=model_id))

    @expose('kajiki:mailtemplates.templates.new_translation')
    @expose('genshi:mailtemplates.templates.new_translation')
    def edit_translation(self, translation_id, **kwargs):
        __, translations = model.provider.query(model.TemplateTranslation, filters=dict(_id=translation_id))
        if not translations:
            return tg.abort(404)
        translation = translations[0]
        return dict(form=EditTranslationForm, values=dict(translation_id=translation._id,
                                                            language=translation.language,
                                                            subject=translation.subject,
                                                            body=translation.body))

    @expose()
    @validate(CreateTranslationForm, error_handler=new_translation)
    def create_translation(self, **kwargs):
        __, mail_models = model.provider.query(model.MailModel, filters=dict(_id=kwargs.get('model_id')))
        if not mail_models:
            return tg.abort(404)
        mail_model = mail_models[0]
        new_translation = model.provider.create(model.TemplateTranslation, dict(language=kwargs.get('language'),
                                                                                mail_model=mail_model,
                                                                                subject=kwargs.get('subject'),
                                                                                body=kwargs.get('body')))
        tg.flash(_('Translation created.'))
        return redirect(url('index'))

    @expose()
    @validate(EditTranslationForm, error_handler=edit_translation)
    def update_translation(self, **kwargs):
        __, translations = model.provider.query(model.TemplateTranslation, filters=dict(_id=kwargs.get('translation_id')))
        if not translations:
            return tg.abort(404)
        model.provider.update(model.TemplateTranslation, dict(_id=kwargs.get('translation_id'),
                                                              language=kwargs.get('language'),
                                                              subject=kwargs.get('subject'),
                                                              body=kwargs.get('body')), omit_fields=['mail_model'])
        tg.flash(_('Translation edited.'))
        return redirect(url('index'))

    @expose('kajiki:mailtemplates.templates.new_model')
    @expose('genshi:mailtemplates.templates.new_model')
    def new_model(self, **kwargs):
        default_language = config['_mailtemplates']['default_language']
        return dict(form=NewModelForm, values=dict(language=default_language))


    @expose()
    @validate(NewModelForm, error_handler=new_model)
    def create_model(self, **kwargs):
        mail_model = model.provider.create(model.MailModel, dict(name=kwargs.get('name'), usage=kwargs.get('usage')))
        new_translation = model.provider.create(model.TemplateTranslation, dict(language=kwargs.get('language'),
                                                                                mail_model=mail_model,
                                                                                subject=kwargs.get('subject'),
                                                                                body=kwargs.get('body')))
        tg.flash(_('Model created.'))
        return redirect(url('index'))

    @expose('kajiki:mailtemplates.templates.new_translation')
    @expose('genshi:mailtemplates.templates.new_translation')
    @validate(CreateTranslationForm, error_handler=new_translation)
    def validate_template(self, **kwargs):
        tg.flash("Email template valid.")
        return dict(form=CreateTranslationForm, values=kwargs)

    @expose('kajiki:mailtemplates.templates.new_translation')
    @expose('genshi:mailtemplates.templates.new_translation')
    @validate(EditTranslationForm, error_handler=edit_translation)
    def validate_template_edit(self, **kwargs):
        tg.flash("Email template valid.")
        return dict(form=EditTranslationForm, values=kwargs)

    @expose('kajiki:mailtemplates.templates.new_translation')
    @expose('genshi:mailtemplates.templates.new_translation')
    @validate(NewModelForm, error_handler=new_model)
    def validate_template_model(self, **kwargs):
        tg.flash("Email template valid.")
        return dict(form=NewModelForm, values=kwargs)
