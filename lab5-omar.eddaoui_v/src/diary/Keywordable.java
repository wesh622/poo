package diary;

import java.util.List;

public interface Keywordable {
    void addKeyword(String keyword);
    void removeKeyword(String keyword);
    int keywordsCount();
    List<String> getKeywords();
}
