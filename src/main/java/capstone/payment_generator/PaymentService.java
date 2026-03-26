package capstone.payment_generator;

import jakarta.websocket.SendResult;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j //로그 기록
public class PaymentService {
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final String TOPIC = "payment-events";

    public void send(PaymentEvent event){
        kafkaTemplate.send(TOPIC, event.getTransactionId(), event)
                        .whenComplete((result, ex) -> {
                            if (ex == null) {
                                log.info("[결제발생] 거래ID: {} | 계좌: {} | 유저: {} | 금액: {}원 | 시간: {} | IP: {} | 기기: {} | Partition: {} | Offset: {}",
                                        event.getTransactionId(),
                                        event.getAccountNo(),
                                        event.getUserId(),
                                        String.format("%,d", event.getAmount()),
                                        event.getTimestamp(),
                                        event.getIpAddress(),
                                        event.getDeviceId(),
                                        result.getRecordMetadata().partition(),
                                        result.getRecordMetadata().offset()
                                        );
                            }else {
                                log.error("❌ [Kafka Failed] TransactionId: {} | Reason: {}",
                                        event.getTransactionId(), ex.getMessage(), ex);

                            }
                        });

    }

}
