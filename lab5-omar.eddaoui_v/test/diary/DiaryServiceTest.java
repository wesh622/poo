package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethod;
import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredMethodWithReturnType;

public class DiaryServiceTest {

	@Test
	public void testGetTitle() {
		assertDeclaredMethod("diary.DiaryService", "getTitle", new String[] {},
				"missing method getTitle() in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "getTitle", new String[] { }, "java.lang.String",
				"missing method getTitle() in interface DiaryService");
	}

	@Test
	public void testPost() {
		assertDeclaredMethod("diary.DiaryService", "post", new String[] { "diary.Attributable" },
				"missing method post(Attributable) in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "post", new String[] { "diary.Attributable" }, "void",
				"missing method post(Attributable) in interface DiaryService");
	}

	@Test
	public void testGetItems() {
		assertDeclaredMethod("diary.DiaryService", "getEntries", new String[] {},
				"missing method getItems() in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "getEntries", new String[] {}, "java.util.List",
				"missing method getItems() in interface DiaryService");
		// TODO: check return type is 'List<Publishable>'
	}

	@Test
	public void testGetPublishableItemsCount() {
		assertDeclaredMethod("diary.DiaryService", "getEntriesCount", new String[] {},
				"missing method getEntriesCount() in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "getEntriesCount", new String[] {}, "int",
				"missing method getEntriesCount() in interface DiaryService");
	}

	@Test
	public void testGetTaggableItemsCount() {
		assertDeclaredMethod("diary.DiaryService", "getKeywordableEntriesCount", new String[] {},
				"missing method getKeywordableEntriesCount() in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "getKeywordableEntriesCount", new String[] {}, "int",
				"missing method getKeywordableEntriesCount() in interface DiaryService");
	}

	@Test
	public void testFindItemsByAuthor() {
		assertDeclaredMethod("diary.DiaryService", "findEntriesByAuthor", new String[] { "java.lang.String" },
				"missing method findEntriesByAuthor(String) in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "findEntriesByAuthor", new String[] { "java.lang.String" }, "java.util.List",
				"missing method findEntriesByAuthor(String) in interface DiaryService");
		// TODO: check return type is 'List<Publishable>'
	}

	@Test
	public void testGetLatestItem() {
		assertDeclaredMethod("diary.DiaryService", "getLatestEntry", new String[] {},
				"missing method getLatestEntry() in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "getLatestEntry", new String[] {}, "diary.Timestampable",
				"missing method getLatestEntry() in interface DiaryService");
	}

	@Test
	public void testFindItemsByTags() {
		assertDeclaredMethod("diary.DiaryService", "findEntriesByKeywords", new Class<?>[] { String[].class },
				"missing method findEntriesByKeywords(String[]) in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "findEntriesByKeywords", new Class[] { String[].class }, "java.util.List",
				"missing method findEntriesByKeywords(String[]) in interface DiaryService");
		// TODO: check return type is 'List<Publishable>'
	}

	@Test
	public void testFindItemsByContent() {
		assertDeclaredMethod("diary.DiaryService", "findEntriesByContent", new Class<?>[] { String[].class },
				"missing method findEntriesByContent(String[]) in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "findEntriesByContent", new Class<?>[] { String[].class }, "java.util.List",
				"missing method findEntriesByContent(String[]) in interface DiaryService");
		// TODO: check return type is 'List<Publishable>'
	}

	@Test
	public void testFindItemsByTagsOrContent() {
		assertDeclaredMethod("diary.DiaryService", "findEntriesByKeywordsOrContent", new Class<?>[] { String[].class },
				"missing method findEntriesByKeywordsOrContent(String[]) in interface DiaryService");
		assertDeclaredMethodWithReturnType("diary.DiaryService", "findEntriesByKeywordsOrContent", new Class<?>[] { String[].class }, "java.util.List",
				"missing method findEntriesByKeywordsOrContent(String[]) in interface DiaryService");
		// TODO: check return type is 'List<Publishable>'
	}

}
