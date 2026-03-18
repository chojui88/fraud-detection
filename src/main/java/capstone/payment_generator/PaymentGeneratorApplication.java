package capstone.payment_generator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
public class PaymentGeneratorApplication {

	public static void main(String[] args) {
		SpringApplication.run(PaymentGeneratorApplication.class, args);
	}

}
