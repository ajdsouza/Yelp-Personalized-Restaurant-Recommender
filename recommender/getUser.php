<?php 
    if (isset($_POST['user_id'])) {
        $db = new SQLite3('Data/datatouille.db');
        $results = $db->query("SELECT user_id,name,average_stars,review_count FROM yelp_users WHERE user_id LIKE '".$_POST["user_id"]."'");
        while ($row = $results->fetchArray()) {
          echo "<div class=\"userName\">User: ".$row["name"]."</div>";
          echo "<div class=\"averageRating\">Average Rating: ".$row["average_stars"]."</div>";
          echo "<div class=\"numReviews\">Number of Reviews: ".$row["review_count"]."</div>";
        }
    } else {
      echo "Incorrect Inputs";
    }
?>
