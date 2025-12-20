# --- Stage 1: Build Stage ---
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

# --- Stage 2: Runtime Stage ---
FROM eclipse-temurin:17-jre
LABEL maintainer="heating-monitor-devops"
WORKDIR /app

# --- SECURITY UPDATE: Create non-root user ---
RUN groupadd -r spring && useradd -r -g spring spring

COPY --from=builder /app/target/*.jar app.jar

RUN chown spring:spring app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# --- SECURITY UPDATE: Switch context ---
USER spring:spring

ENTRYPOINT ["java", "-jar", "app.jar"]
