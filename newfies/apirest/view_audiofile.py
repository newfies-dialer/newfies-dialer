# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from apirest.audiofile_serializers import AudioFileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_audio.forms import DialerAudioFileForm
from audiofield.models import AudioFile
from permissions import CustomObjectPermissions


class AudioFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows audio_files to be viewed or edited.
    """
    model = AudioFile
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the audio files
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = AudioFile.objects.all()
        else:
            queryset = AudioFile.objects.filter(user=self.request.user)
        return queryset

    def create(self, request):
        """Customize create"""
        queryset = AudioFile.objects.all()
        request.DATA['convert_type'] = settings.CONVERT_TYPE_VALUE
        request.DATA['channel_type'] = settings.CHANNEL_TYPE_VALUE
        request.DATA['freq_type'] = settings.FREQ_TYPE_VALUE
        form = DialerAudioFileForm(request.DATA, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            queryset = AudioFile.objects.filter(pk=obj.id)

        serializer = AudioFileSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Customize update"""
        pk = kwargs['pk']
        queryset = AudioFile.objects.filter(id=pk)
        obj = get_object_or_404(AudioFile, id=pk, user=request.user)

        request.DATA['convert_type'] = settings.CONVERT_TYPE_VALUE
        request.DATA['channel_type'] = settings.CHANNEL_TYPE_VALUE
        request.DATA['freq_type'] = settings.FREQ_TYPE_VALUE
        form = DialerAudioFileForm(request.DATA, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            queryset = AudioFile.objects.filter(id=pk)

        serializer = AudioFileSerializer(queryset, many=True)
        return Response(serializer.data)
