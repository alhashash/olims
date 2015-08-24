"""Generic field extensions
"""
from dependencies.dependency import aq_inner
from dependencies.dependency import aq_parent
from dependencies.dependency import Implicit
from dependencies.dependency import ImplicitAcquisitionWrapper
from archetypes.schemaextender.interfaces import IExtensionField
from dependencies.dependency import *
from dependencies.dependency import DateTimeField
from dependencies.dependency import RecordField, RecordsField
from dependencies.dependency import implements
from dependencies.dependency import getSite

class ExtensionField(object):

    """Mix-in class to make Archetypes fields not depend on generated
    accessors and mutators, and use AnnotationStorage by default.

    """

    implements(IExtensionField)

    storage = AnnotationStorage()

    def getAccessor(self, instance):
        def accessor():
            if self.getType().endswith('ReferenceField'):
                return self.get(instance.__of__(getSite()))
            else:
                return self.get(instance)
        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor():
            if self.getType().endswith('ReferenceField'):
                return self.getRaw(instance.__of__(getSite()))
            else:
                return self.getRaw(instance)
        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            if self.getType().endswith('ReferenceField'):
                self.set(instance.__of__(getSite()), value)
            else:
                self.set(instance, value)
        return mutator

    def getIndexAccessor(self, instance):
        name = getattr(self, 'index_method', None)
        if name is None or name == '_at_accessor':
            return self.getAccessor(instance)
        elif name == '_at_edit_accessor':
            return self.getEditAccessor(instance)
        elif not isinstance(name, basestring):
            raise ValueError('Bad index accessor value: %r', name)
        else:
            return getattr(instance, name)

class ExtBooleanField(ExtensionField, BooleanField):

    "Field extender"


class ExtComputedField(ExtensionField, ComputedField):

    "Field extender"


class ExtDateTimeField(ExtensionField, DateTimeField):

    "Field extender"


class ExtFloatField(ExtensionField, FloatField):

    "Field extender"


class ExtIntegerField(ExtensionField, IntegerField):

    "Field extender"


class ExtLinesField(ExtensionField, LinesField):

    "Field extender"


class ExtRecordField(ExtensionField, RecordField):

    "Field extender"


class ExtRecordsField(ExtensionField, RecordsField):

    "Field extender"


class ExtReferenceField(ExtensionField, ReferenceField):

    "Field extender"


class ExtStringField(ExtensionField, StringField):

    "Field extender"


class ExtTextField(ExtensionField, TextField):

    "Field extender"

# #
# # Method Initialization
# # apply default getters and setters to schemaextender fields.
# #

# def generateMethods(context, fields):
#     for field in fields:
#         name = field.getName()
#         if getattr(context, 'get'+name, None) is None:
#             if field.getType().find("Reference") > -1:
#                 setattr(context, 'get'+name,
#                         context.Schema()[name].getAccessor(
#                                                     context.__of__(getSite())))
#             else:
#                 setattr(context, 'get'+name,
#                         context.Schema()[name].getMutator(context))
#         if getattr(context, 'set'+name, None) is None:
#             if field.getType().find("Reference") > -1:
#                 setattr(context, 'set'+name,
#                         context.Schema()[name].getMutator(
#                                                     context.__of__(getSite())))
#             else:
#                 setattr(context, 'set'+name,
#                         context.Schema()[name].getMutator(context))
#         if field.getType().find("Reference") > -1:
#             setattr(context, name, atapi.ATReferenceFieldProperty(fieldname))
#         else:
#             setattr(context, name, atapi.ATFieldProperty(fieldname))

# class field_getter:
#     def __init__(self, context, fieldname):
#         self.context = context
#         self.fieldname = fieldname
#     def __call__(self, **kwargs):
#         return self.context.Schema()[self.fieldname].getAccessor(self.context)(**kwargs)

# class field_setter:
#     def __init__(self, context, fieldname):
#         self.context = context
#         self.fieldname = fieldname
#     def __call__(self, value, **kwargs):
#         return self.context.Schema()[self.fieldname].getMutator(self.context)(value, **kwargs)
