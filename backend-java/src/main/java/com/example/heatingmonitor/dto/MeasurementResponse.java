package com.example.heatingmonitor.dto;
import java.time.Instant;
import java.util.UUID;

public record MeasurementResponse(UUID id, Double temperature, String deviceId, Instant createdAt) {}
