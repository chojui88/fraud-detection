package capstone.payment_generator;

import lombok.RequiredArgsConstructor;
import org.apache.kafka.common.protocol.types.Field;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
@RequiredArgsConstructor
public class PaymentScheduler {
    private final PaymentService paymentService;

    //파레토 법칙 8:2 유저 생성
    private String generateUserId() {
        double probability = Math.random();
        int userIndex;
        if (probability < 0.8) {
            userIndex = (int) (Math.random() * 1000);
        } else {
            userIndex = (int) (Math.random() * 100000);
        }
        return "USER_" + userIndex;
    }

    @Scheduled(fixedRate = 1000) // 1초마다 실행
    public void generateData() {
        // 한번에 실행될 때 10건씩 반복문
        for (int i = 0; i < 10; i++) {
            PaymentEvent event = new PaymentEvent(
                    "JUI_" + UUID.randomUUID().toString().substring(0, 8).toUpperCase(), // 거래번호
                    "302-" + (int) (Math.random() * 9000 + 1000) + "-11",   // 계좌번호
                    generateUserId(),   //사용자 ID
                    (long) (Math.random() * 100000), // 결제 금액 최대 10만원
                    System.currentTimeMillis(), // 현재 시간
                    "192.168.0." + (int)(Math.random() * 255),            // 가상 IP 추가
                    "DEV-" + (int)(Math.random() * 5000)        // 가상 기기ID 추가
            );

            paymentService.send(event);



        }
    }
}