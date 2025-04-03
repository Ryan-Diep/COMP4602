import { Rettiwt } from 'rettiwt-api';
import fs from 'fs';

const rettiwt = new Rettiwt({ apiKey: "a2R0PW5zMkNyN3p3NllEb2VuUmpwMW9pb0dWNllRQUJnRGZQVEEwQ0RkMlI7YXV0aF90b2tlbj1lMjBhMjdkMDBjM2M4ZmRiZmY3MDMxZTUwNzI0YTM0ZWYyODgyNjM1O2N0MD02Y2MyOWJkN2YyMGQ5ODk5ODQ2NjBlMWY2MjhlZmYzNTc3Y2YyNTMwZmZkMTg1MTg1N2ViMTgzNjljYWYyOWJhODRjNTM5NDY2MTU4NmJlMzkyYjVhNjU3MjQ3YWIwMGYyNzJhNjE5OGVmYzAwMDBmYjNlODgwMDkzMTFmNDMzMmVmNzBjYWI5OWY1YjYyZGVhYTM5OGNmZTZjODA1ZDY2O3R3aWQ9dSUzRDQ1MTg1MzI4ODI7"
});

const inputFilePath = '../output.json';

const data = fs.readFileSync(inputFilePath, 'utf8');
const jsonData = JSON.parse(data);

const outputFilePath = '../user_metrics.json';
let outputData = [];
outputData = fs.existsSync(outputFilePath)
    ? JSON.parse(fs.readFileSync(outputFilePath, "utf8"))
    : [];

async function fetchUser(id, count, nextCursor) {
    rettiwt.user
            .following(id, count, nextCursor)
            .then((res) => {
                if (res !== undefined) {
                // console.log(res);
                outputData.push({user_id: id, res}); 
                fs.writeFileSync(
                    outputFilePath,
                    JSON.stringify(outputData, null, 2),
                    "utf8"
                );
                
                } else {
                // console.log(res);
                outputData.push({ user_id: id, error: "null" });
                fs.writeFileSync(
                    outputFilePath,
                    JSON.stringify(outputData, null, 2),
                    "utf8"
                );
                }
            })
            .catch((err) => {
                console.log(err);
                // if (err.message === "TOO_MANY_REQUESTS") {
                //     console.log("Rate limit hit. Waiting for 10 seconds...");
                //     new Promise((resolve) => setTimeout(resolve, 10000)).then(() => {
                //         console.log("Retrying...");
                //     }
                // }
            });
}
async function processUsers(){
    for (const user of jsonData) {
        if (outputData.some(existingItem => existingItem.id === user.tweetBy.id)) {
            console.log(`Skipping tweet with id: ${user.tweetBy.id} as it already exists in the output.`);
            continue;
        } else {
            let randomDelay = Math.round(10000 + (15000 - 10000) * (Math.random() + Math.random() - 1) / 2);
            await new Promise((resolve) => setTimeout(resolve, randomDelay)); // Wait for 2 second
            let response = fetchUser(user.tweetBy.id, 100, null);
            console.log(response.list);
        }
    }
}
processUsers()

// fetchUser('1299475694573977600', 100, null)

// const fetchAllFollowers = async (userId, count, nextCursor) => {

//     let response = await rettiwt.user.following(userId,count, nextCursor);
//     let followers = response.list;

//     console.log(response.next.value)
//     // console.log(response.list[1].userName)

//     total+=followers.length;

//     console.log("Current:",followers.length)
//     console.log("Total:",total)

//     if (response.next.value !== '0|0') {
//         followers = followers.concat((await fetchAllFollowers(userId, count,  response.next.value)));
//     }

//     return followers;
// }
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

// fetchUser('476213099', 100, null)

async function processUsers(){
    for (const user of jsonData) {
        if (outputData.some(existingItem => existingItem.id === user.tweetBy.id)) {
            console.log(`Skipping tweet with id: ${user.tweetBy.id} as it already exists in the output.`);
            continue;
        } else {
            let randomDelay = Math.round(10000 + (15000 - 10000) * (Math.random() + Math.random() - 1) / 2);
            await new Promise((resolve) => setTimeout(resolve, randomDelay)); // Wait for 2 second
            let response = fetchUser(user.tweetBy.id, 100, null);
            console.log(response.list);
        }
    }
}

// if user has err key then we skip the user
processUsers()