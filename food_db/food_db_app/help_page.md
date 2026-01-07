# Help and Guides

## Pages
Use the navigation bar to access different sections:

- **Home**: If you record when you cook meals, the Home page shows dashboards with charts and statistics about your cooking patterns
- **Add a new recipe**: Create and save new recipes
- **Recipes**: Search and filter your recipe collection
- **Food Manager**: Manage food items and categorize them, allowing you to create organized grocery shopping lists
- **Bulk Prep**: Plan a feast! If you plan to cook multiple meals for a holiday or dinner party, Bulk Prep will help you choose your meals, build a grocery list, and coordinate their timing

## Tags

You can create tags for your recipes that help you search for them later. Create as many or as few tags as you want. Some example tags might be "Pasta", "Weeknights", "Cold weather", "Sweet", etc. Tags are created on the "Add a new recipe" page. When creating a tag, you can choose the color scheme of your tag so it's visually easier to distinguish them in your search result.

## Cooking vs Baking Mode

You basically have two Food DBs in that your cooking and baking recipes are kept separately. Some pages (adding/editing recipes, searching for recipes) have a toggle switch at the top that lets you switch between Cooking and Baking. In addition to changing the color theme, the Cooking/Baking divide does a few things:

1. When adding/editing a recipe, change the toggle switch (and therefore color scheme) to either Cooking or Baking to determine where this recipe is stored in your database.
2. On the Recipes page, when searching for recipes, toggle this switch to search either the Cooking or Baking recipes in your database.
3. When creating a tag (done on the add/edit recipe page), you can choose if the tag is only relevant for Cooking, for Baking, or for both. Tags being relevant for both won't cause any database crossover - it just means you can tag Cooking recipes and Baking recipes with this tag.

## Cooking Meals

On a recipe's detail page, there's a button in the upper right that allows you to mark that recipe as "cooked". This records in your database that you cooked the recipe today (if you need to edit the date, you can do so via the admin panel). This doesn't functionally do much for you, it's just to collect the data. But having that data does two things: it populates the Home page with graphs about your cooking habits, and it shows the number of times cooked on the Recipes page. By sorting the "Times cooked" and "Last cooked" columns on the Recipes page, you can find your favorites, recipes that need love, or a recipe you haven't cooked in a long time.

## Grocery Lists and the Food Manager

When viewing a recipe for which you've entered ingredients, a button appears that says **Show Grocery List**. This will list all the ingredients and do its best to total up quantities and reduce duplicate ingredients. For example, if your recipe needs 2 tbsp of salt for seasoning meat and 1/2 tbsp of salt for your sauce, the grocery list will show 2.5 tbsp of salt. However, it is not yet smart enough to combine different units of measurement, so 2 tbsp of salt and 1 tsp of salt will show up as two different items.

You can take your grocery list to the next level by categorizing the different foods you use for ingredients. Then your grocery list will be organized by food category (Baking, Meat, Dairy, etc.) to make your shopping trip a little more efficient. Your Food DB comes pre-loaded with hundreds of foods that are already categorized, which you can see on the Food Manager page. 

The Food Manager page shows - in addition to the pre-loaded foods - every food you've ever used for an ingredient in a recipe. Whenever you use an unrecognized food as an ingredient, the food gets added to this list without a category. You can come to this page to categorize it. You can also rename and merge foods, which automatically updates recipes that use them. For example, if you have "basil" and "basil leaves" as two different foods, you can merge the two together so all recipes using "basil leaves" will now use "basil". If you want to modify the food categories, you'll have to do it via your admin panel.

The default behavior of the Food DB is, when you create an ingredient using a food that's never been used before, a new food is added to the Food Manager. However, you can [configure your Food DB to suggest similar existing foods](https://github.com/liveandletbri/food_db?tab=readme-ov-file#environment-variables) when you create something new, or have you confirm that the new food is indeed worth saving.

## Bulk Prep

Planning a Thanksgiving Feast? Choosing which Christmas cookies to make this year? You will want a variety of flavors, and you may need to plan the order in which you cook everything so you don't have to raise then lower the oven temperature. This is where the Bulk Prep tab can help you!

From the Recipes page or from an individual recipe's detail page, you can add recipes to your cart. The number of recipes in your cart shows up in the navbar at the top. Visit the Bulk Prep page to see all the recipes in your cart compared to each other.

### Tag matrix
By default, the first table will show each recipe in your cart on the rows, and each tag that those recipes have in the columns. This can help you see redundancies in your feast. You don't want too many Sweet tags without a Savory (or do you?)!

You can configure this matrix to have a preset list of tags though, which can also help you identify the absence of a recipe with a tag. Maybe your cart is only Sweets and you want to make sure that Savory is still included in the table. To configure the tag list, head to the [View Config tab](#view-config).

### Attribute matrix
Similarly to the tag matrix, the attribute matrix will show different attributes of your recipes. The default is to show oven temperature plus all the timing attributes, but like the tag matrix, this is configurable in the [View Config tab](#view-config).

### View Config
Choose the tags and attributes you want in your matrices here, and save the list as a new View Config. This records your preferences in the database and saves your selected config in your sessoin cookies. You can always come back to this tab to edit a View Config if you need to.

## Linking Ingredients to Steps
When you create a recipe you might notice that, in your step description, some of the ingredient names are underlined and some are not. This is Step-Ingredient Linking, and it does two things: first, when you hover over the underlined ingredient name, it shows you the quantity and any notes you had from the Ingredients table, so you don't have to keep scrolling up and down. Second, if you are in Cooking Mode, when you check off a step, it will also check off any linked inredients in the Ingredients table.

So why are only _some_ of your ingredients underlined? When you first create a recipe (not when you edit it later), the Food DB scans your steps for exact name matches of ingredients, and then creates this link for you. If your Ingredient list says "shredded cheddar" and you mention "shredded cheddar" in your steps, the link will be created automatically. However, if you instead just wrote "the cheese" in your steps, the link will not automatically be created. There is a syntax you can use to manually create these links for any ingredient that the automatic links missed, and you can learn about that by hovering your mouse over the Help icon next to the Steps header.

## Searching Recipes

Use the Recipes page to search and filter your recipes. You can:

- Search by text in recipe titles or the ingredients
- Filter including tags and/or excluding them
- Filter by the total cooking duration
- Sort your results by creation date, last cooked date, or number of times cooked
- Apply multiple filters to narrow down results

## Adding Recipes

Create new recipes by adding:

- Recipe title and description
- Ingredients with quantities and units
- Step-by-step instructions
- Images
- Tags for organization
- Timing information (prep time, cook time, etc.)

