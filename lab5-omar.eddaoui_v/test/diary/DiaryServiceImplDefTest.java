package diary;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.ReflectionAssertions.assertDeclaredConstructor;


public class DiaryServiceImplDefTest {
	
	@Test
	public void testDeclaredConstructors() {		
		assertDeclaredConstructor("diary.DiaryServiceImpl", new String[] { "java.lang.String" }, "missing constructor DiartServiceImpl(String) in class DiartServiceImpl");
	}
	
}
