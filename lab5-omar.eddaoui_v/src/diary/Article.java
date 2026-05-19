package diary;

public class Article extends AbstractEntry {
    private String body;

    public Article(long date,String author,String body){
        super(date, author);
        this.body = body;
    }
    public String getContent(){
        return this.body;
    }
}
