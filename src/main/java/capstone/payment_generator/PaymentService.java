package capstone.payment_generator;

import lombok.RequiredArgsConstructor;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PaymentService {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void send(PaymentEvent event){
        kafkaTemplate.send("payment-logs",event);
    }

}
