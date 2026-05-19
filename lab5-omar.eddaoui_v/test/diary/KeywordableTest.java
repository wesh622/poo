package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;

import java.util.List;

public class KeywordableTest {

	@Test
	public void testAddKeyword() {
		assertDeclaredMethod("diary.Keywordable", "addKeyword", new String[] { "java.lang.String" }, "missing method addKeyword(String) in interface Keywordable");		
		assertDeclaredMethodWithReturnType("diary.Keywordable", "addKeyword", new String[] { "java.lang.String" }, "void", "missing method addKeyword(String) in interface Keywordable");		
	}

	@Test
	public void testRemoveKeyword() {
		assertDeclaredMethod("diary.Keywordable", "removeKeyword", new String[] { "java.lang.String" }, "missing method removeKeyword(String) in interface Keywordable");		
		assertDeclaredMethodWithReturnType("diary.Keywordable", "removeKeyword", new String[] { "java.lang.String" }, "void", "missing method removeKeyword(String) in interface Keywordable");		
	}

	@Test
	public void testKeywordsCount() {
		assertDeclaredMethod("diary.Keywordable", "keywordsCount", new String[] {}, "missing method keywordsCount() in interface Keywordable");
		assertDeclaredMethodWithReturnType("diary.Keywordable", "keywordsCount", new String[] {}, "int", "missing method keywordsCount() in interface Keywordable");
	}

	@Test
	public void testGetKeywords() {
		assertDeclaredMethod("diary.Keywordable", "getKeywords", new String[] {}, "missing method getKeywords() in interface Keywordable");
		assertDeclaredMethodWithReturnType("diary.Keywordable", "getKeywords", new String[] {}, List.class, "missing method getKeywords() in interface Keywordable");
	}
}
