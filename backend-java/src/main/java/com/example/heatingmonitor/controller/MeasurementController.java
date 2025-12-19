package com.example.heatingmonitor.controller;

import com.example.heatingmonitor.dto.CreateMeasurementRequest;
import com.example.heatingmonitor.dto.MeasurementResponse;
import com.example.heatingmonitor.service.MeasurementService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/measurements")
@RequiredArgsConstructor
public class MeasurementController {

    private final MeasurementService service;

    @PostMapping
    public ResponseEntity<MeasurementResponse> createMeasurement(@Valid @RequestBody CreateMeasurementRequest request) {
        MeasurementResponse response = service.recordMeasurement(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping
    public ResponseEntity<List<MeasurementResponse>> getMeasurements() {
        return ResponseEntity.ok(service.getRecentMeasurements());
    }
}
