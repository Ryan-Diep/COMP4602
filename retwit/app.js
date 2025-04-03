import { Rettiwt } from 'rettiwt-api';
import fs from 'fs';
// const fs = require('fs');
// import data from '../train.json';
// Creating a new Rettiwt instance using the given 'API_KEY'
const rettiwt = new Rettiwt({ apiKey: "a2R0PW5zMkNyN3p3NllEb2VuUmpwMW9pb0dWNllRQUJnRGZQVEEwQ0RkMlI7YXV0aF90b2tlbj1lMjBhMjdkMDBjM2M4ZmRiZmY3MDMxZTUwNzI0YTM0ZWYyODgyNjM1O2N0MD02Y2MyOWJkN2YyMGQ5ODk5ODQ2NjBlMWY2MjhlZmYzNTc3Y2YyNTMwZmZkMTg1MTg1N2ViMTgzNjljYWYyOWJhODRjNTM5NDY2MTU4NmJlMzkyYjVhNjU3MjQ3YWIwMGYyNzJhNjE5OGVmYzAwMDBmYjNlODgwMDkzMTFmNDMzMmVmNzBjYWI5OWY1YjYyZGVhYTM5OGNmZTZjODA1ZDY2O3R3aWQ9dSUzRDQ1MTg1MzI4ODI7"
});

const filePath = '../train.json';
const coaidFilePath = '../coaid.json';

const data = fs.readFileSync(filePath, 'utf8');
const coaidData = fs.readFileSync(coaidFilePath, 'utf8');

const jsonData = JSON.parse(data);
const coaidJsonData = JSON.parse(coaidData);

// Append the response to a JSON file
const outputFilePath = '../coAid-output.json';
let outputData = [];
outputData = fs.existsSync(outputFilePath)
    ? JSON.parse(fs.readFileSync(outputFilePath, "utf8"))
    : [];

async function processTweets() {
    for (const item of jsonData) {
        if (outputData.some(existingItem => existingItem.id === item.tweet_id)) {
            console.log(`Skipping tweet with id: ${item.tweet_id} as it already exists in the output.`);
            continue;
        } else {
            let randomDelay = Math.round(10000 + (15000 - 10000) * (Math.random() + Math.random() - 1) / 2);
            await new Promise((resolve) => setTimeout(resolve, randomDelay)); // Wait for 2 second
            rettiwt.tweet
            .details(item.tweet_id)
            .then((res) => {
              if (res !== undefined) {
                console.log(res);

                outputData.push(res);
                fs.writeFileSync(
                  outputFilePath,
                  JSON.stringify(outputData, null, 2),
                  "utf8"
                );
              } else {
                console.log(res);
                outputData.push({ id: item.tweet_id, error: "null" });
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
    }
}
let counter = 0;
async function processTweetsCoaid() {
    for (const item of coaidJsonData) {
        if (outputData.some(existingItem => existingItem.id === item.tweet_id)) {
            console.log(`Skipping tweet with id: ${item.tweet_id} as it already exists in the output.`);
            counter++;
            continue;
        } else {
            let randomDelay = Math.round(10000 + (15000 - 10000) * (Math.random() + Math.random() - 1) / 2);
            await new Promise((resolve) => setTimeout(resolve, randomDelay)); // Wait for 2 second
            rettiwt.tweet
            .details(item.tweet_id)
            .then((res) => {
              if (res !== undefined) {
                console.log(res);
                outputData.push(res);
                counter++;
                fs.writeFileSync(
                  outputFilePath,
                  JSON.stringify(outputData, null, 2),
                  "utf8"
                );
              } else {
                console.log(res);
                outputData.push({ id: item.tweet_id, error: "null" });
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
            console.log(counter);
        }
        if (counter >= 200) {
            console.log("Processed 100 tweets, stopping further processing.");
            break; // Stop processing after 100 tweets
        }
    }
}

processTweetsCoaid(); // Call the function to process tweets