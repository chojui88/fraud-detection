package capstone.payment_generator;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;


@Data
@AllArgsConstructor
@NoArgsConstructor
public class PaymentEvent {
    private String transactionId; // 거래번호
    private String accountNo; //계좌번호
    private String userId;
    private long amount; //결제금액
    private long timestamp; // 시간
    private String ipAddress;      // 접속 IP
    private String deviceId;       // 기기 식별값



}
