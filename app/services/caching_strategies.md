# Caching Strategies

## 1.Cache-Aside

- In this strategy, the application is responsible for managing the cache. When data is requested, the application checks the cache first. If the data is not in the cache, it is retrieved from the database and stored in the cache for future use. This strategy is simple and flexible, but it requires careful management of the cache to ensure that it remains up-to-date.

## 2.Write-Through

- In this strategy, data is written to both the cache and the database at the same time. When data is updated, it is written to the cache and the database simultaneously. This ensures that the cache always contains up-to-date data, but it can slow down write operations.

## 3.Write-Behind

- In this strategy, data is written to the cache first and then to the database at a later time. This allows write operations to be faster, but it can lead to data inconsistencies if the cache is not properly managed.

## 4. Read-Through

- In this strategy, the cache is used as the primary data source. When data is requested, the cache is checked first. If the data is not in the cache, it is retrieved from the database and stored in the cache for future use. This strategy can be useful when the database is slow or when data is frequently read but rarely updated.

Please note #2 -> #4 are not done in the application layer
