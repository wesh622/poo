package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;

public class AbstractMediaDefTest {

	@Test	
	public void testAddKeyword() {
		assertDeclaredMethod("diary.AbstractMedia", "addKeyword", new String[] { "java.lang.String" }, "missing method addKeyword(String) in class AbstractMedia");
		assertDeclaredMethodWithReturnType("diary.AbstractMedia", "addKeyword", new String[] { "java.lang.String" }, "void", "missing method addKeyword(String) in class AbstractMedia");
	}

	@Test
	public void testRemoveKeyword() {
		assertDeclaredMethod("diary.AbstractMedia", "removeKeyword", new String[] { "java.lang.String" }, "missing method removeKeyword(String) in class AbstractMedia");		
		assertDeclaredMethodWithReturnType("diary.AbstractMedia", "removeKeyword", new String[] { "java.lang.String" }, "void", "missing method removeKeyword(String) in class AbstractMedia");		
	}

	@Test
	public void testKeywordsCount() {
		assertDeclaredMethod("diary.AbstractMedia", "keywordsCount", new String[] { }, "missing method keywordsCount() in class AbstractMedia");		
		assertDeclaredMethodWithReturnType("diary.AbstractMedia", "keywordsCount", new String[] { }, "int", "missing method keywordsCount() in class AbstractMedia");		
	}

	@Test
	public void testGetKeywords() {
		assertDeclaredMethod("diary.AbstractMedia", "getKeywords", new String[] { }, "missing method getKeywords() in class AbstractMedia");		
		assertDeclaredMethodWithReturnType("diary.AbstractMedia", "getKeywords", new String[] { }, "java.util.List", "missing method getKeywords() in class AbstractMedia");		
		// TODO: check return type is 'List<String>'
	}

	@Test
	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.AbstractMedia", new String[] { "long", "java.lang.String" }, "missing constructor AbstractMedia(long, String) in class AbstractMedia");
	}
}
