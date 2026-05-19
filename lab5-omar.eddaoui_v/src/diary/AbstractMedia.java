package diary;

import java.util.ArrayList;
import java.util.List;

public abstract class AbstractMedia extends AbstractEntry implements Keywordable{
    private ArrayList<String> liste;

    public AbstractMedia(long date,String author){
        super(date, author);
        this.liste = new ArrayList<>();
    }

    public void addKeyword(String keyword){
        if(!this.liste.contains(keyword)){
            this.liste.add(keyword);
        }
    }

    public void removeKeyword(String keyword){
        this.liste.remove(keyword);
    }

    public int keywordsCount(){
        return this.liste.size();
    }

    public List<String> getKeywords(){
        if(this.liste == null){
            ArrayList<String> s = new ArrayList<String>();
            return s;
        }
        else{
           return this.liste; 
        }
    }
    
}
