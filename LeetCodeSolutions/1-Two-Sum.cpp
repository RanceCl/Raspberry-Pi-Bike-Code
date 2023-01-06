/* 
This function takes in an array of integers and a target sum and find the two integers that will add together into the sum.
The indices of these two numbers would be returned in a vector.

In order to make the code faster, inputs were sorted so the code could iterate from the beginning and end.

Assume that each vector and target will have exactly one solution.

Time Complexity: O(NlogN)
Space Complexity: O(N)
*/
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        vector<int> nums_sorted;
        vector<int> addends;
        int i, j=0;
        int index1=0, index2=nums.size()-1;

        /* Sort the input integer array */
        nums_sorted = nums;
        sort(nums_sorted.begin(), nums_sorted.end());   //Sort the number array for future 
        
        /* Loop through the vector to find the addends */
        while(index1<index2)
        {
            //If the addends equal the target, exit the while loop 
            if( (nums_sorted[index1]+nums_sorted[index2]) == target )
                break;
            //If the current numbers are smaller than the target, the lower addend must be increased
            else if( (nums_sorted[index1]+nums_sorted[index2]) < target )
                index1++;
            //If the current numbers are larger than the target, the higher addend must be decreased
            else
                index2--;
        }

        /* Find the original indices of the addend values */
        for(i=0; i<nums_sorted.size(); i++)
        {
            //push_back is used to ensure that the index of the first addend encountered is placed first in the solution
            if( nums_sorted[index1] == nums[i] )
                addends.push_back(i);
            else if( nums_sorted[index2] == nums[i] )
                addends.push_back(i);
        }

        return addends;
    }
};
