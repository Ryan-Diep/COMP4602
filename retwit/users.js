import { Rettiwt } from 'rettiwt-api';
import fs from 'fs';

const rettiwt = new Rettiwt({ apiKey: "a2R0PW5zMkNyN3p3NllEb2VuUmpwMW9pb0dWNllRQUJnRGZQVEEwQ0RkMlI7YXV0aF90b2tlbj1lMjBhMjdkMDBjM2M4ZmRiZmY3MDMxZTUwNzI0YTM0ZWYyODgyNjM1O2N0MD02Y2MyOWJkN2YyMGQ5ODk5ODQ2NjBlMWY2MjhlZmYzNTc3Y2YyNTMwZmZkMTg1MTg1N2ViMTgzNjljYWYyOWJhODRjNTM5NDY2MTU4NmJlMzkyYjVhNjU3MjQ3YWIwMGYyNzJhNjE5OGVmYzAwMDBmYjNlODgwMDkzMTFmNDMzMmVmNzBjYWI5OWY1YjYyZGVhYTM5OGNmZTZjODA1ZDY2O3R3aWQ9dSUzRDQ1MTg1MzI4ODI7"
});

const inputFilePath = '../coAid-output.json';

const userMetricsFilePath = '../coAid_user_metrics.json';

const data = fs.readFileSync(inputFilePath, 'utf8');
const jsonData = JSON.parse(data);


const outputFilePath = '../users_following.json';
let outputData = [];
outputData = fs.existsSync(outputFilePath)
    ? JSON.parse(fs.readFileSync(outputFilePath, "utf8"))
    : [];

// async function processUsers() {
//     for (const user of jsonData) {
//         if (user.tweetBy === undefined) {
//             console.log("Skipping user as tweetBy is undefined:", user);
//             continue;
//         }

//         if (outputData.some(existingItem => existingItem.user_id === user.tweetBy.id)) {
//             console.log(`Skipping user with id: ${user.tweetBy.id} as it already exists in the output.`);
//             continue;
//         }

//         try {
//             // Introduce a random delay to avoid rate-limiting
//             let randomDelay = Math.round(10000 + (15000 - 10000) * (Math.random() + Math.random() - 1) / 2);
//             await new Promise((resolve) => setTimeout(resolve, randomDelay));

//             // First API call: Fetch following
//             const followingRes = await rettiwt.user.following(user.tweetBy.id, 100, null);
//             const followingList = followingRes.list.map((item) => {
//                 const firstKey = Object.keys(item)[0];
//                 return { [firstKey]: item[firstKey] };
//             });

//             // Second API call: Fetch followers
//             const followersRes = await rettiwt.user.followers(user.tweetBy.id, 100, null);
//             const followersList = followersRes.list.map((item) => {
//                 const firstKey = Object.keys(item)[0];
//                 return { [firstKey]: item[firstKey] };
//             });

//             // Push the combined output to outputData
//             outputData.push({
//                 user_id: user.tweetBy.id,
//                 following: followingList,
//                 followers: followersList,
//             });

//             // Write the updated outputData to the file
//             fs.writeFileSync(
//                 outputFilePath,
//                 JSON.stringify(outputData, null, 2),
//                 "utf8"
//             );

//         } catch (err) {
//             console.log(`Error processing user with id ${user.tweetBy.id}:`, err.message);
//             outputData.push({ user_id: user.tweetBy.id, error: err.message });
//             fs.writeFileSync(
//                 outputFilePath,
//                 JSON.stringify(outputData, null, 2),
//                 "utf8"
//             );
//         }
//     }
// }
// processUsers()

async function fetchWithCursor(apiFunction, userId, cursor = null, accumulatedData = []) {
    try {
        // Wait for 2 seconds before making the API call
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Make the API call with the cursor
        const response = await apiFunction(userId, 100, null);
            console.log("yup");
        if (response) {
          const followingList = response.list.map((item) => {
            const firstKey = Object.keys(item)[0];
            return { [firstKey]: item[firstKey] };
          });
          // Accumulate the data from the current response
          if (followingList) {
            accumulatedData.push({ followingList });
          }
        } else {
            // if (response === undefined) {
            console.log("Skipping user as response is undefined:", user);
            return accumulatedData;
            // }
        }
    
        // Check if there is a next cursor
        if (response.next) {
            console.log(`Fetching next page with cursor: ${response.next}`);
            // Recursively call the function with the next cursor
            return await fetchWithCursor(apiFunction, userId, response.next, accumulatedData);
        } else {
            console.log(`Finished processing user ${userId}`);
        }

        // Return the accumulated data when no more pages are available
        return accumulatedData;
    } catch (err) {
        console.error(`Error fetching data for user ${userId}:`, err.message);
        return accumulatedData; // Return whatever data has been accumulated so far
    }
}

// Example usage
async function processUser(userId) {
    const followingData = await fetchWithCursor(rettiwt.user.following, userId);
    // const followersData = await fetchWithCursor(rettiwt.user.followers, userId);

    console.log(`User ${userId} - Following:`, followingData);
    // console.log(`User ${userId} - Followers:`, followersData);

    // You can now process or save the data as needed
    outputData.push({
        user_id: userId,
        following: followingData,
        // followers: followersData,
    });

    fs.writeFileSync(outputFilePath, JSON.stringify(outputData, null, 2), "utf8");
}
let total = 0
const fetchAllFollowers = async (userId, count, nextCursor = null) => {

    let response = await rettiwt.user.following(userId, count, nextCursor);
    // let followers = response.list;
    let followers = response.list.map((item) => {
        const firstKey = Object.keys(item)[0];
        return { [firstKey]: item[firstKey] };
    });

    // const followingList = followingRes.list.map((item) => {
    //                     const firstKey = Object.keys(item)[0];
    //                     return { [firstKey]: item[firstKey] };
    //                 });

    // console.log(response.next.value)
    //console.log(response.list[1].userName)
    console.log(userId)
    total+=followers.length;

    console.log("Current:", followers.length)
    console.log("Total:",total)
    // if (response.next.value === '0|0') {
    //     outputData.push({
    //         user_id: userId,
    //         followers: followers
    //     });

    //     fs.writeFileSync(outputFilePath, JSON.stringify(outputData, null, 2), "utf8");
    // }
    if (followers.length !== 0) {
    //   console.log(response.next.value);
      await new Promise((resolve) => {
        setTimeout(resolve, 2000);
      });
      followers = followers.concat(
        await fetchAllFollowers(userId, 50, response.next.value)
      );
      
      console.log(followers);
    }

    return followers;
}

async function myfunction() {
// Call the function for a specific user
    for (const user of jsonData) {
        // for (const otherUser of jsonData) {
        // if(user === otherUser) {
        //     continue;
        // }
        
        // processUser(user.tweetBy.id);
        if(user.tweetBy === undefined) {
            console.log("Skipping user as tweetBy is undefined:", user);
            continue;

        } 
        if (outputData.some(existingItem => existingItem.user_id === user.tweetBy.id)) {
            console.log(`Skipping user with id: ${user.tweetBy.id} as it already exists in the output.`);
            continue;
        }else{
            await new Promise((resolve) => {setTimeout(resolve, 2000);});
            outputData.push({user_id: user.tweetBy.id,followingList:await fetchAllFollowers(user.tweetBy.id, 100, null)})
            
            fs.writeFileSync(outputFilePath, JSON.stringify(outputData, null, 2), "utf8");
            // break; // Remove this line if you want to process all users
        }
        
        // }
    }
}
myfunction();
// for (const user of jsonData) {
//     fetchAllFollowers(user.tweetBy.id, 100, null)
//         // .then(res => {
//         //     console.log(res);
//         //     outputData.push(res); 
//         //     fs.writeFileSync(
//         //         outputFilePath,
//         //         JSON.stringify(outputData, null, 2),
//         //         "utf8"
//         //     );
//         // })
//         // .catch(err => {
//         //     console.log(err);
//         // });
//     break;
// }


// fs.writeFileSync(outputFilePath, JSON.stringify(outputData, null, 2), 'utf8');
// processUsers()


// Fetching the first 100 following of the User with id '1234567890'
// rettiwt.user.following('476213099')
// .then(res => {
//     console.log(res.list);
// })
// .catch(err => {
//     console.log(err);
// });

// for (const user of jsonData) {
//     rettiwt.user.following(user.tweetBy.id, 1)
//     .then(res => {
//         console.log(res);
//         // if (res.next) {
//         //     rettiwt.user.following(user.tweetBy.id, 100, res.next)
//         //     .then(res => {
//         //         console.log(res);
//         //     })
//         //     .catch(err => {
//         //         console.log(err);
//         //     });
//         // }
//         console.log(res.next);
//     })
    
//     .catch(err => {
//         console.log(err);
//     });
    

//     // console.log(user.tweetBy.id);
//     break;
// }