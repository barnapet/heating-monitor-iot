CREATE TABLE measurements (
    id UUID NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    device_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT pk_measurements PRIMARY KEY (id)
);

CREATE INDEX idx_measurements_created_at ON measurements (created_at);
