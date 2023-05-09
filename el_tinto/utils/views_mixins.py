class SerializerByActionMixin:
    def get_serializer_class(self):
        return getattr(self, "serializer_class_%s" % (self.action.lower(),))
