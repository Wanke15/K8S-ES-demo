kubectl delete service es-poi
kubectl expose deployment es-poi --port=9292 --target-port=9200 --type=LoadBalancer
