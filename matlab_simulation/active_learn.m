function [all_predictions, eval] = active_learn(X, Y, bootstrap_size, step_size, budget)

% Start with an initial sample
eval = [];
all_predictions = [];
N = size(Y, 1);
sample_perm = randperm(N);
sample = sample_perm(1:bootstrap_size);
% sample = (1:bootstrap_size);

% Train a logistic model on the initial sample
model = logistic(X(sample,3:end),Y(sample));
predictions = 1./(1+exp(-X(1:N,3:end)*model));
predictionvar = predictions;
predictions = (predictions >= .5);

% Evaluate the model (normalized L1 error)
% Don't throw away our training labels when taking sums
% predictions(sample) = labels(sample); 
eval = [eval eval_model_sum(predictions, Y)];
all_predictions = [all_predictions predictions];

% Iterate on active learning, using a simple uncertainty criterion
% to select new points for training
num_iters = (budget - bootstrap_size) / step_size;
for k=1:num_iters
    disp(['finished ', num2str(k), ' of ', num2str(num_iters+1), ' iterations...'])
	remaining = setdiff((1:N)',sample);
    
    % uncertainty is the distance from the logistic's decision boundary
    [~, i] = sort(abs(predictionvar(remaining)-.5)); 
    
    % add the new sample
    sample = [sample remaining(i(1:step_size))'];
    
    % retrain the model
    model = logistic(X(sample,3:end), Y(sample));
    predictions = 1./(1+exp(-X(1:N,3:end)*model));
    predictionvar = predictions;
    predictions = (predictions >= .5);
   
    %predictions(sample) = Y(sample);
    eval = [eval eval_model_sum(predictions, Y)];
    all_predictions = [all_predictions predictions];
end

figure;
plot(bootstrap_size:step_size:budget, eval, 'gs-');
