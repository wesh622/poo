package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;

public class TimestampableTest {

    @Test
    void testGetPublicationDate() {
        assertDeclaredMethod("diary.Timestampable", "getTimestamp", new String[] {}, "missing method getTimestamp() in interface Timestampable");
        assertDeclaredMethodWithReturnType("diary.Timestampable", "getTimestamp", new String[] {}, "long", "missing method getTimestamp() in interface Timestampable");
    }

}


