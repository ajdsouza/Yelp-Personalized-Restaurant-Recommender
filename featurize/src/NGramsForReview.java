import java.io.*;

/**
 * Given a new review text this method extracts n-grams and
 * their corresponding feature vectors.
 */
public class NGramsForReview {
    public static void main(String[] args) {

        RemoteHelper gen = new RemoteHelper();
        RemoteHelper.ReturnData returnData = new RemoteHelper.ReturnData();

        System.out.println("Input review text: " + args[0]);

        try {
            gen.processReviewText(args[0], returnData, "", null, null);
        } catch (IOException e) {
            e.printStackTrace();
        }

        String retVal = "";
        for (int i = 0; i < returnData.featureVector.size(); i++) {
            String featureVect = "";
            int [] currFeatureVec = returnData.featureVector.get(i);

            for (int j = 0; j < currFeatureVec.length; j++) {
                featureVect += currFeatureVec[j] + ",";
            }
            featureVect = featureVect.substring(0, featureVect.length() -1);

            retVal += returnData.dishNames.get(i).trim() + "|" + featureVect + "\n";
        }
        System.out.println("n-grams and features: ");
        System.out.println(retVal);

    }
}