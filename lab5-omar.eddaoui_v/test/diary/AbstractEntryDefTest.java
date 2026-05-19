package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;

public class AbstractEntryDefTest {

	@Test	
	public void testGetAuthor() {		
        assertDeclaredMethod("diary.AbstractEntry", "getAuthor", new String[] {}, "missing method getAuthor() in class AbstractEntry");
        assertDeclaredMethodWithReturnType("diary.AbstractEntry", "getAuthor", new String[] {}, "java.lang.String", "missing method getAuthor() in class AbstractEntry");
	}

	@Test
	public void testGetTimestamp() {
        assertDeclaredMethod("diary.AbstractEntry", "getTimestamp", new String[] {}, "missing method getTimestamp() in class AbstractEntry");
        assertDeclaredMethodWithReturnType("diary.AbstractEntry", "getTimestamp", new String[] {}, "long", "missing method getTimestamp() in class AbstractEntry");
	}

	@Test
	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.AbstractEntry", new String[] { "long", "java.lang.String" }, "missing constructor AbstractEntry(long, String) in class AbstractEntry");
	}

}
