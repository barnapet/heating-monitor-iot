package com.example.heatingmonitor.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public record CreateMeasurementRequest(
    @NotNull(message = "Temperature is required")
    @Min(-50) @Max(100)
    Double temperature,

    @NotNull(message = "Device ID is required")
    String deviceId
) {}
