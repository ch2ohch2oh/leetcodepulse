const test = require('node:test');
const assert = require('node:assert/strict');
const {
    aggregateData,
    chartWindow,
    getBucketStart
} = require('../static/aggregation.js');

function sample(timestamp, total) {
    return { timestamp, total_submissions: total };
}

test('aggregates regular samples into local hourly buckets', () => {
    const data = [
        sample('2026-01-15T10:00:00-05:00', 100),
        sample('2026-01-15T11:00:00-05:00', 160),
        sample('2026-01-15T12:00:00-05:00', 250)
    ];
    const result = aggregateData(data, 'hour');

    assert.deepEqual(result.map(point => point.value), [60, 90]);
    assert.deepEqual(result.map(point => point.estimated), [false, false]);
});

test('marks buckets estimated when a long collection gap crosses them', () => {
    const data = [
        sample('2026-01-15T10:00:00-05:00', 100),
        sample('2026-01-15T17:00:00-05:00', 800)
    ];
    const result = aggregateData(data, 'hour');

    assert.equal(result.length, 7);
    assert.ok(result.every(point => point.estimated));
    assert.deepEqual(result.map(point => point.value), Array(7).fill(100));
});

test('does not mark a long gap estimated when it stays within one displayed bucket', () => {
    const data = [
        sample('2026-01-15T10:00:00-05:00', 100),
        sample('2026-01-15T17:00:00-05:00', 800)
    ];
    const result = aggregateData(data, 'day');

    assert.equal(result.length, 1);
    assert.equal(result[0].value, 700);
    assert.equal(result[0].estimated, false);
});

test('ignores a counter regression and its recovery instead of creating a spike', () => {
    const data = [
        sample('2026-01-15T10:00:00-05:00', 1000),
        sample('2026-01-15T11:00:00-05:00', 1100),
        sample('2026-01-15T12:00:00-05:00', 50),
        sample('2026-01-15T13:00:00-05:00', 500),
        sample('2026-01-15T14:00:00-05:00', 1100),
        sample('2026-01-15T15:00:00-05:00', 1150)
    ];
    const result = aggregateData(data, 'hour');

    assert.deepEqual(result.map(point => point.value), [100, 50]);
});

test('excludes incomplete buckets and limits the hourly view to seven days', () => {
    const points = [];
    const start = new Date('2026-01-01T00:00:00-05:00').getTime();
    for (let hour = 0; hour < 10 * 24; hour += 1) {
        points.push({ timestamp: new Date(start + hour * 60 * 60 * 1000), value: hour });
    }
    const latestSample = new Date(points[points.length - 1].timestamp.getTime() + 30 * 60 * 1000);
    const result = chartWindow(points, 'hour', latestSample);

    assert.equal(result.at(-1).timestamp.getTime(), points.at(-2).timestamp.getTime());
    assert.ok(result.at(-1).timestamp.getTime() - result[0].timestamp.getTime() <= 7 * 24 * 60 * 60 * 1000);
});

test('uses the viewer local timezone for bucket boundaries', () => {
    const timestamp = new Date('2026-01-15T10:42:00-05:00').getTime();
    const start = new Date(getBucketStart(timestamp, 'day'));

    assert.equal(start.getHours(), 0);
    assert.equal(start.getDate(), 15);
});
