plt = [];

sample = (1:100);

crowd_votes = V(sample,:);

model = logistic(dataset(sample,3:end),gt(sample));

predictions = 1./(1+exp(-dataset(1:1000,3:end)*model));

predictionvar = predictions;

predictions = (predictions >= .5);

predictions(sample) = gt(sample);

 

plt = [plt abs(sum(predictions) - sum(gt))/sum(gt)];

 

for k=2:1:19

    remaining = setdiff((1:1000)',sample);

    [v i] = sort(abs(predictionvar(remaining)-.5));

    sample = [sample remaining(i(1:50))'];

    crowd_votes = V(sample,:);

    model = logistic(dataset(sample,3:end),gt(sample));

    predictions = 1./(1+exp(-dataset(1:1000,3:end)*model));

    predictionvar = predictions;

    predictions = (predictions >= .5);

    predictions(sample) = gt(sample);

    plt = [plt abs(sum(predictions) - sum(gt))/sum(gt)];

end

plot(plt, 'gs-');