from rest_framework import serializers

class CoreSerializer(serializers.ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the CoreSerializer with optional field filtering.
        This method customizes the serializer to only include specific fields
        if the 'fields' parameter is provided in kwargs.
        Args:
            *args: Variable length argument list passed to parent initializer
            **kwargs: Arbitrary keyword arguments
                        - fields (list, optional): List of field names to include in the serializer.
                        If provided, only these fields will be kept in the serializer.
        Note:
            The 'fields' parameter is popped from kwargs before passing to the parent initializer.
            If 'fields' is provided, any field not in the list will be removed from the serializer.
        """
        fields = kwargs.pop('fields', None)
        super(CoreSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class CoreModelSerializer(CoreSerializer):
    created_by = serializers.ReadOnlyField()
    modified_by = serializers.ReadOnlyField()
