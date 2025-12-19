package com.example.heatingmonitor.repository;

import com.example.heatingmonitor.domain.TemperatureMeasurement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface MeasurementRepository extends JpaRepository<TemperatureMeasurement, UUID> {
    // Később ide jönnek a time-series lekérdezések (pl. findAllByCreatedAtBetween...)
}
