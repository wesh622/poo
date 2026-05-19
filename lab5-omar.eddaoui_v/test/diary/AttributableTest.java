package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;

public class AttributableTest {

    @Test
    void testGetAuthor() {
        assertDeclaredMethod("diary.Attributable", "getAuthor", new String[] {}, "missing method getAuthor() in interface Attributable");
        assertDeclaredMethodWithReturnType("diary.Attributable", "getAuthor", new String[] {}, "java.lang.String", "missing method getAuthor() in interface Attributable");
    }

}


