package com.example.heatingmonitor.service;

import com.example.heatingmonitor.domain.TemperatureMeasurement;
import com.example.heatingmonitor.dto.CreateMeasurementRequest;
import com.example.heatingmonitor.dto.MeasurementResponse;
import com.example.heatingmonitor.repository.MeasurementRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class MeasurementService {

    private final MeasurementRepository repository;

    @Transactional
    public MeasurementResponse recordMeasurement(CreateMeasurementRequest request) {
        TemperatureMeasurement entity = new TemperatureMeasurement(
            request.temperature(),
            request.deviceId()
        );
        TemperatureMeasurement saved = repository.save(entity);
        return new MeasurementResponse(saved.getId(), saved.getTemperature(), saved.getDeviceId(), saved.getCreatedAt());
    }

    @Transactional(readOnly = true)
    public List<MeasurementResponse> getRecentMeasurements() {
        return repository.findAll().stream() // Ide később pagináció kell!
                .map(this::mapToResponse)
                .toList();
    }

    private MeasurementResponse mapToResponse(TemperatureMeasurement entity) {
        return new MeasurementResponse(
            entity.getId(),
            entity.getTemperature(),
            entity.getDeviceId(),
            entity.getCreatedAt()
        );
    }
}
